using UnityEngine;
using UnityEngine.Rendering.Universal;

public class DebugURPActiveRenderer : MonoBehaviour
{
    void Start()
    {
        var cam = Camera.main;
        if (cam == null)
        {
            Debug.LogError("DebugURP: No Camera.main found.");
            return;
        }

        var camData = cam.GetUniversalAdditionalCameraData();

        // Force camera to use the pipeline default renderer (index -1 means default).
        camData.SetRenderer(-1);

        var urpAsset = UniversalRenderPipeline.asset;
        Debug.Log($"DebugURP: URP Asset = {(urpAsset ? urpAsset.name : "NULL")}");

        var renderer = camData.scriptableRenderer;
        Debug.Log($"DebugURP: Camera renderer = {(renderer != null ? renderer.GetType().Name : "NULL")}");

        // Try to print the renderer name if possible
        Debug.Log($"DebugURP: Camera renderPostProcessing = {camData.renderPostProcessing}");
        Debug.Log($"DebugURP: Camera allowXRRendering = {camData.allowXRRendering}");
    }
}
