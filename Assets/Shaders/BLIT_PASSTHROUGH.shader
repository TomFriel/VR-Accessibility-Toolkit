Shader "CVD/BLIT_PASSTHROUGH"
{
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Overlay" }

        Pass
        {
            Name "BlitPassthrough"
            ZTest Always
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Common.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/TextureXR.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/GlobalSamplers.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/UnityInstancing.hlsl"

            // Bound by URP Full Screen Pass when "Fetch Color Buffer" is enabled
            TEXTURE2D_X(_BlitTexture);

            struct Attributes
            {
                uint vertexID : SV_VertexID;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv         : TEXCOORD0;
            };

            Varyings Vert(Attributes v)
            {
                Varyings o;

                float2 uv2 = float2((v.vertexID << 1) & 2, v.vertexID & 2);

                // 0..1 UVs
                o.uv = uv2 * 0.5;

                o.positionCS = float4(uv2 * 2.0 - 1.0, 0.0, 1.0);
                return o;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                return SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, i.uv);
            }

            ENDHLSL
        }
    }

    Fallback Off
}
