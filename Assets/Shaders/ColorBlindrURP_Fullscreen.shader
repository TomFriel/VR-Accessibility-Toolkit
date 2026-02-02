Shader "CVD/ColorBlindrURP_Fullscreen"
{
    Properties
    {
        _Mode("Mode (0=Normal,1=Protan,2=Deutan,3=Tritan)", Float) = 0
        _Strength("Strength", Range(0,1)) = 1
    }

    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Overlay" }

        Pass
        {
            Name "ColorBlindr URP Fullscreen"
            ZTest Always
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D_X(_BlitTexture);
            SAMPLER(sampler_BlitTexture);

            CBUFFER_START(UnityPerMaterial)
                float _Mode;
                float _Strength;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv         : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float2 uv          : TEXCOORD0;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes v)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);

                // Fullscreen mesh usually supplies clip-space in POSITION
                o.positionHCS = float4(v.positionOS.xy, 0.0, 1.0);
                o.uv = v.uv;
                return o;
            }

            // ---- sRGB <-> Linear helpers (no Unity dependency) ----
            float3 SRGBToLinear_Approx(float3 c)
            {
                // IEC 61966-2-1:1999
                float3 lo = c / 12.92;
                float3 hi = pow((c + 0.055) / 1.055, 2.4);
                return lerp(hi, lo, step(c, 0.04045));
            }

            float3 LinearToSRGB_Approx(float3 c)
            {
                float3 lo = c * 12.92;
                float3 hi = 1.055 * pow(max(c, 0.0), 1.0 / 2.4) - 0.055;
                return lerp(hi, lo, step(c, 0.0031308));
            }

            // ===== ColorBlindr math (ported from ColorBlindr.shader) =====
            float3 rgb2lin(float3 c) { return (0.992052 * pow(c, 2.2) + 0.003974) * 128.498039; }
            float3 lin2rgb(float3 c) { return pow(c, 0.45454545); }

            float3 rgFilter(float3 color, float k1, float k2, float k3, float strength)
            {
                color = saturate(color);
                float3 c_lin = rgb2lin(color);

                float r_blind = (k1 * c_lin.r + k2 * c_lin.g) / 16448.25098;
                float b_blind = (k3 * c_lin.r - k3 * c_lin.g + 128.498039 * c_lin.b) / 16448.25098;
                r_blind = saturate(r_blind);
                b_blind = saturate(b_blind);

                float3 simulated = lin2rgb(float3(r_blind, r_blind, b_blind));
                return lerp(color, simulated, strength);
            }

            float3 tritanFilter(float3 color, float strength)
            {
                color = saturate(color);

                float anchor_e0 = 0.05059983 + 0.08585369 + 0.00952420;
                float anchor_e1 = 0.01893033 + 0.08925308 + 0.01370054;
                float anchor_e2 = 0.00292202 + 0.00975732 + 0.07145979;
                float inflection = anchor_e1 / anchor_e0;

                float a1 = -anchor_e2 * 0.007009;
                float b1 = anchor_e2 * 0.0914;
                float c1 = anchor_e0 * 0.007009 - anchor_e1 * 0.0914;
                float a2 = anchor_e1 * 0.3636 - anchor_e2 * 0.2237;
                float b2 = anchor_e2 * 0.1284 - anchor_e0 * 0.3636;
                float c2 = anchor_e0 * 0.2237 - anchor_e1 * 0.1284;

                float3 c_lin = rgb2lin(color);

                float L = (c_lin.r * 0.05059983 + c_lin.g * 0.08585369 + c_lin.b * 0.00952420) / 128.498039;
                float M = (c_lin.r * 0.01893033 + c_lin.g * 0.08925308 + c_lin.b * 0.01370054) / 128.498039;
                float S = (c_lin.r * 0.00292202 + c_lin.g * 0.00975732 + c_lin.b * 0.07145979) / 128.498039;

                float tmp = M / L;
                if (tmp < inflection) S = -(a1 * L + b1 * M) / c1;
                else                 S = -(a2 * L + b2 * M) / c2;

                float r = L * 30.830854 - M * 29.832659 + S * 1.610474;
                float g = -L * 6.481468 + M * 17.715578 - S * 2.532642;
                float b = -L * 0.375690 - M * 1.199062 + S * 14.273846;

                float3 simulated = lin2rgb(saturate(float3(r, g, b)));
                return lerp(color, simulated, strength);
            }
            // ============================================================

            half4 Frag(Varyings i) : SV_Target
            {
                float3 col = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_BlitTexture, i.uv).rgb;

                // 0 = Normal passthrough
                if (_Mode < 0.5)
                    return half4(col, 1);

                // If project is Linear, convert to sRGB-ish space for ColorBlindr math.
                // If project is Gamma, leave it alone.
                float3 colSRGB = col;
                #if !defined(UNITY_COLORSPACE_GAMMA)
                    colSRGB = LinearToSRGB_Approx(col);
                #endif

                float3 outSRGB = colSRGB;

                // 1 = Protanopia
                if (_Mode < 1.5)
                {
                    outSRGB = rgFilter(colSRGB, 14.443137, 114.054902, 0.513725, _Strength);
                }
                // 2 = Deuteranopia
                else if (_Mode < 2.5)
                {
                    outSRGB = rgFilter(colSRGB, 37.611765, 90.87451, -2.862745, _Strength);
                }
                // 3 = Tritanopia
                else
                {
                    outSRGB = tritanFilter(colSRGB, _Strength);
                }

                // Convert back to Linear if needed
                float3 outCol = outSRGB;
                #if !defined(UNITY_COLORSPACE_GAMMA)
                    outCol = SRGBToLinear_Approx(outSRGB);
                #endif

                return half4(outCol, 1);
            }

            ENDHLSL
        }
    }
}
