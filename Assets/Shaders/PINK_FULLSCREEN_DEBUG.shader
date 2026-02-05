Shader "Debug/PINK_FULLSCREEN_DEBUG"
{
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Overlay" }
        Pass
        {
            Name "Pink"
            ZTest Always
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            struct Attributes { uint vertexID : SV_VertexID; };
            struct Varyings { float4 positionCS : SV_POSITION; };

            Varyings Vert(Attributes i)
            {
                // Fullscreen triangle (no URP includes required)
                Varyings o;
                float2 uv = float2((i.vertexID << 1) & 2, i.vertexID & 2);
                o.positionCS = float4(uv * 2.0 - 1.0, 0.0, 1.0);
                return o;
            }

            float4 Frag(Varyings i) : SV_Target
            {
                return float4(1, 0, 1, 1); // MAGENTA
            }
            ENDHLSL
        }
    }
}
