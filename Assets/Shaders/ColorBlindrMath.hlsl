// Assets/Shaders/ColorBlindrMath.hlsl
#ifndef COLORBLINDR_MATH_INCLUDED
#define COLORBLINDR_MATH_INCLUDED

/*
PSEUDOCODE (clear overview)
--------------------------
- Take the current screen color (URP camera color buffer).
- Convert from linear to gamma-like (because the original ColorBlindr math expects display-space).
- Apply one of the ColorBlindr simulation algorithms based on Mode:
    0 = Normal (no change)
    1 = Deuteranopia (rgFilter with Deuter constants)
    2 = Protanopia  (rgFilter with Protan constants)
    3 = Tritanopia  (tritanFilter)
- Blend between original and simulated using Strength (0..1).
- Convert back to linear for URP output.
- Provide both float and half precision entry points for Shader Graph Custom Function.
*/

#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Common.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Color.hlsl"

// -----------------------------------------------------------------------------
// Core math copied from ColorBlindr.shader (Chman) and adapted for URP fullscreen.
// -----------------------------------------------------------------------------

inline float3 rgb2lin_like_original(float3 c) // Matches ColorBlindr.shader rgb2lin()
{
    // Original: (0.992052 * pow(c, 2.2) + 0.003974) * 128.498039
    return (0.992052 * pow(c, 2.2) + 0.003974) * 128.498039;
}

inline float3 lin2rgb_like_original(float3 c) // Matches ColorBlindr.shader lin2rgb()
{
    // Original: pow(c, 0.45454545)
    return pow(c, 0.45454545);
}

inline float3 rgFilter(float3 colorGamma, float k1, float k2, float k3, float strength) // Simulates red/green deficiencies (Deuter/Protan)
{
    colorGamma = saturate(colorGamma);

    // Convert into the same linear-ish space the original algorithm uses.
    float3 c_lin = rgb2lin_like_original(colorGamma);

    // Compute simulated channels (matches original rgFilter).
    float r_blind = (k1 * c_lin.r + k2 * c_lin.g) / 16448.25098;
    float b_blind = (k3 * c_lin.r - k3 * c_lin.g + 128.498039 * c_lin.b) / 16448.25098;

    r_blind = saturate(r_blind);
    b_blind = saturate(b_blind);

    // Convert back and blend by strength (matches original lerp(color, simulated, _Strength)).
    float3 simulatedGamma = lin2rgb_like_original(float3(r_blind, r_blind, b_blind));
    return lerp(colorGamma, simulatedGamma, saturate(strength));
}

inline float3 tritanFilter(float3 colorGamma, float strength) // Simulates Tritanopia (blue/yellow deficiency)
{
    colorGamma = saturate(colorGamma);

    // Constant setup matches ColorBlindr.shader tritanFilter().
    float anchor_e0 = 0.05059983 + 0.08585369 + 0.00952420;
    float anchor_e1 = 0.01893033 + 0.08925308 + 0.01370054;
    float anchor_e2 = 0.00292202 + 0.00975732 + 0.07145979;
    float inflection = anchor_e1 / anchor_e0;

    float a1 = -anchor_e2 * 0.007009;
    float b1 =  anchor_e2 * 0.0914;
    float c1 =  anchor_e0 * 0.007009 - anchor_e1 * 0.0914;
    float a2 =  anchor_e1 * 0.3636 - anchor_e2 * 0.2237;
    float b2 =  anchor_e2 * 0.1284 - anchor_e0 * 0.3636;
    float c2 =  anchor_e0 * 0.2237 - anchor_e1 * 0.1284;

    float3 c_lin = rgb2lin_like_original(colorGamma);

    // LMS-like transform matches the original shader.
    float L = (c_lin.r * 0.05059983 + c_lin.g * 0.08585369 + c_lin.b * 0.00952420) / 128.498039;
    float M = (c_lin.r * 0.01893033 + c_lin.g * 0.08925308 + c_lin.b * 0.01370054) / 128.498039;
    float S = (c_lin.r * 0.00292202 + c_lin.g * 0.00975732 + c_lin.b * 0.07145979) / 128.498039;

    // Original uses tmp = M / L (no guard). Kept the same for functional parity.
    float tmp = M / L;

    // Branch and solve for S matches the original shader.
    if (tmp < inflection) S = -(a1 * L + b1 * M) / c1;
    else                 S = -(a2 * L + b2 * M) / c2;

    // Convert back to RGB and blend by strength (matches original).
    float r =  L * 30.830854 - M * 29.832659 + S *  1.610474;
    float g = -L *  6.481468 + M * 17.715578 - S *  2.532642;
    float b = -L *  0.375690 - M *  1.199062 + S * 14.273846;

    float3 simulatedGamma = lin2rgb_like_original(saturate(float3(r, g, b)));
    return lerp(colorGamma, simulatedGamma, saturate(strength));
}

// -----------------------------------------------------------------------------
// Shader Graph entry points (Custom Function node)
// -----------------------------------------------------------------------------

void ColourBlindApply_float(float3 In, float Mode, float Strength, out float3 Out) // Applies selected simulation mode to screen color
{
    float m = floor(Mode + 0.5);
    float s = saturate(Strength);

    // URP camera color is typically linear; convert to gamma-like before running the original algorithm.
    float3 inGamma = LinearToSRGB(saturate(In));

    float3 resultGamma = inGamma;

    // Mode mapping for this project (single-pass switch instead of multi-pass shader).
    if (m < 0.5)
    {
        // 0 = Normal
        resultGamma = inGamma;
    }
    else if (m < 1.5)
    {
        // 1 = Deuteranopia (matches ColorBlindr pass constants)
        resultGamma = rgFilter(inGamma, 37.611765, 90.87451, -2.862745, s);
    }
    else if (m < 2.5)
    {
        // 2 = Protanopia (matches ColorBlindr pass constants)
        resultGamma = rgFilter(inGamma, 14.443137, 114.054902, 0.513725, s);
    }
    else
    {
        // 3 = Tritanopia (matches ColorBlindr pass constants)
        resultGamma = tritanFilter(inGamma, s);
    }

    // Convert back to linear for URP output.
    Out = SRGBToLinear(saturate(resultGamma));
}

void ColourBlindApply_half(half3 In, half Mode, half Strength, out half3 Out) // Half-precision wrapper for Shader Graph compatibility
{
    float3 o;
    ColourBlindApply_float((float3)In, (float)Mode, (float)Strength, o);
    Out = (half3)o;
}

#endif
