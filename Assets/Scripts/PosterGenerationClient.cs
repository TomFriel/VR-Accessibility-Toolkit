using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class PosterGenerationClient : MonoBehaviour
{
    [Header("API Settings")]
    public string apiUrl = "http://127.0.0.1:8000/generate";
    public string templateType = "enemy_ally";

    [Header("Input")]
    public Texture2D sourceTexture;

    [Header("Poster hookup")]
    public AccessibilityPoster linkedPoster;
    public AccessibilityManager accessibilityManager;

    [Header("Optional preview target")]
    public Renderer targetRenderer;
    public Material matNormal;

    [Header("Per-CVD Fix Materials")]
    public Material matFixDeutan;
    public Material matFixProtan;
    public Material matFixTritan;

    [Header("Per-CVD Fix+ Materials")]
    public Material matFixPlusDeutan;
    public Material matFixPlusProtan;
    public Material matFixPlusTritan;

    [Header("Debug Textures")]
    public Texture2D detectedTexture;
    public Texture2D fixDeutanTexture;
    public Texture2D fixProtanTexture;
    public Texture2D fixTritanTexture;
    public Texture2D fixPlusDeutanTexture;
    public Texture2D fixPlusProtanTexture;
    public Texture2D fixPlusTritanTexture;

    [Serializable]
    public class ApiResponse
    {
        public string template_type;
        public string detected_base64;

        public string fix_deutan_base64;
        public string fix_protan_base64;
        public string fix_tritan_base64;

        public string fixplus_deutan_base64;
        public string fixplus_protan_base64;
        public string fixplus_tritan_base64;

        public Metadata metadata;
    }

    [Serializable]
    public class Metadata
    {
        public string template;
        public DetectedObject[] objects;
    }

    [Serializable]
    public class DetectedObject
    {
        public string label;
        public int x;
        public int y;
        public int w;
        public int h;
        public int cx;
        public int cy;
    }

    public void GeneratePosterOutputs()
    {
        Debug.Log("GeneratePosterOutputs called.");

        if (sourceTexture == null)
        {
            Debug.LogError("No sourceTexture assigned.");
            return;
        }

        StartCoroutine(SendImageToApi());
    }

    IEnumerator SendImageToApi()
    {
        Debug.Log("Starting API send...");

        Texture2D readableCopy = MakeTextureReadableCopy(sourceTexture);

        if (readableCopy == null)
        {
            Debug.LogError("Failed to make readable copy of source texture.");
            yield break;
        }

        byte[] pngBytes = readableCopy.EncodeToPNG();

        if (pngBytes == null || pngBytes.Length == 0)
        {
            Debug.LogError("Failed to encode source texture to PNG.");
            yield break;
        }

        Debug.Log("PNG bytes length: " + pngBytes.Length);

        WWWForm form = new WWWForm();
        form.AddBinaryData("file", pngBytes, "poster.png", "image/png");
        form.AddField("template_type", templateType);

        using (UnityWebRequest request = UnityWebRequest.Post(apiUrl, form))
        {
            yield return request.SendWebRequest();

            Debug.Log("Request finished. Result: " + request.result);

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("API request failed: " + request.error);

                if (request.downloadHandler != null)
                {
                    Debug.LogError("Server response: " + request.downloadHandler.text);
                }

                yield break;
            }

            string json = request.downloadHandler.text;
            Debug.Log("API response length: " + json.Length);
            Debug.Log("API response preview: " + json.Substring(0, Mathf.Min(300, json.Length)));

            ApiResponse response = JsonUtility.FromJson<ApiResponse>(json);

            if (response == null)
            {
                Debug.LogError("Failed to parse API response.");
                yield break;
            }

            Debug.Log("Parsed response OK.");
            Debug.Log("detected_base64 empty? " + string.IsNullOrEmpty(response.detected_base64));
            Debug.Log("fix_deutan_base64 empty? " + string.IsNullOrEmpty(response.fix_deutan_base64));
            Debug.Log("fix_protan_base64 empty? " + string.IsNullOrEmpty(response.fix_protan_base64));
            Debug.Log("fix_tritan_base64 empty? " + string.IsNullOrEmpty(response.fix_tritan_base64));
            Debug.Log("fixplus_deutan_base64 empty? " + string.IsNullOrEmpty(response.fixplus_deutan_base64));
            Debug.Log("fixplus_protan_base64 empty? " + string.IsNullOrEmpty(response.fixplus_protan_base64));
            Debug.Log("fixplus_tritan_base64 empty? " + string.IsNullOrEmpty(response.fixplus_tritan_base64));

            detectedTexture = Base64ToTexture(response.detected_base64);

            fixDeutanTexture = Base64ToTexture(response.fix_deutan_base64);
            fixProtanTexture = Base64ToTexture(response.fix_protan_base64);
            fixTritanTexture = Base64ToTexture(response.fix_tritan_base64);

            fixPlusDeutanTexture = Base64ToTexture(response.fixplus_deutan_base64);
            fixPlusProtanTexture = Base64ToTexture(response.fixplus_protan_base64);
            fixPlusTritanTexture = Base64ToTexture(response.fixplus_tritan_base64);

            Debug.Log("detectedTexture null? " + (detectedTexture == null));
            Debug.Log("fixDeutanTexture null? " + (fixDeutanTexture == null));
            Debug.Log("fixProtanTexture null? " + (fixProtanTexture == null));
            Debug.Log("fixTritanTexture null? " + (fixTritanTexture == null));
            Debug.Log("fixPlusDeutanTexture null? " + (fixPlusDeutanTexture == null));
            Debug.Log("fixPlusProtanTexture null? " + (fixPlusProtanTexture == null));
            Debug.Log("fixPlusTritanTexture null? " + (fixPlusTritanTexture == null));

            Debug.Log("matNormal assigned? " + (matNormal != null));
            Debug.Log("matFixDeutan assigned? " + (matFixDeutan != null));
            Debug.Log("matFixProtan assigned? " + (matFixProtan != null));
            Debug.Log("matFixTritan assigned? " + (matFixTritan != null));
            Debug.Log("matFixPlusDeutan assigned? " + (matFixPlusDeutan != null));
            Debug.Log("matFixPlusProtan assigned? " + (matFixPlusProtan != null));
            Debug.Log("matFixPlusTritan assigned? " + (matFixPlusTritan != null));

            ApplyTextureToMaterial(matNormal, sourceTexture);

            ApplyTextureToMaterial(matFixDeutan, fixDeutanTexture);
            ApplyTextureToMaterial(matFixProtan, fixProtanTexture);
            ApplyTextureToMaterial(matFixTritan, fixTritanTexture);

            ApplyTextureToMaterial(matFixPlusDeutan, fixPlusDeutanTexture);
            ApplyTextureToMaterial(matFixPlusProtan, fixPlusProtanTexture);
            ApplyTextureToMaterial(matFixPlusTritan, fixPlusTritanTexture);

            Debug.Log("Applied textures to materials.");

            if (targetRenderer != null && matNormal != null)
            {
                targetRenderer.material = matNormal;
            }

            if (linkedPoster != null)
            {
                linkedPoster.RefreshNow();
                Debug.Log("linkedPoster refreshed.");
            }
            else
            {
                Debug.LogWarning("linkedPoster is null.");
            }

            if (accessibilityManager == null)
            {
                accessibilityManager = FindFirstObjectByType<AccessibilityManager>();
            }

            if (accessibilityManager != null)
            {
                accessibilityManager.RefreshPosters();
                Debug.Log("accessibilityManager refreshed posters.");
            }
            else
            {
                Debug.LogWarning("accessibilityManager is null.");
            }

            SaveTextureIfPossible(detectedTexture, "detected_output.png");
            SaveTextureIfPossible(fixDeutanTexture, "fix_deutan_output.png");
            SaveTextureIfPossible(fixProtanTexture, "fix_protan_output.png");
            SaveTextureIfPossible(fixTritanTexture, "fix_tritan_output.png");
            SaveTextureIfPossible(fixPlusDeutanTexture, "fixplus_deutan_output.png");
            SaveTextureIfPossible(fixPlusProtanTexture, "fixplus_protan_output.png");
            SaveTextureIfPossible(fixPlusTritanTexture, "fixplus_tritan_output.png");

            Debug.Log("Poster generation complete.");
        }
    }

    void ApplyTextureToMaterial(Material mat, Texture2D tex)
    {
        if (mat == null)
        {
            Debug.LogWarning("ApplyTextureToMaterial skipped because material is null.");
            return;
        }

        if (tex == null)
        {
            Debug.LogWarning("ApplyTextureToMaterial skipped because texture is null for material: " + mat.name);
            return;
        }

        mat.mainTexture = tex;

        if (mat.HasProperty("_BaseMap"))
        {
            mat.SetTexture("_BaseMap", tex);
        }

        if (mat.HasProperty("_BaseColor"))
        {
            mat.SetColor("_BaseColor", Color.white);
        }

        if (mat.HasProperty("_Color"))
        {
            mat.SetColor("_Color", Color.white);
        }

        Debug.Log("Applied texture to material: " + mat.name);
    }

    Texture2D MakeTextureReadableCopy(Texture2D source)
    {
        if (source == null)
        {
            return null;
        }

        RenderTexture rt = RenderTexture.GetTemporary(
            source.width,
            source.height,
            0,
            RenderTextureFormat.ARGB32
        );

        Graphics.Blit(source, rt);

        RenderTexture previous = RenderTexture.active;
        RenderTexture.active = rt;

        Texture2D readable = new Texture2D(source.width, source.height, TextureFormat.RGBA32, false);
        readable.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        readable.Apply();

        RenderTexture.active = previous;
        RenderTexture.ReleaseTemporary(rt);

        return readable;
    }

    Texture2D Base64ToTexture(string base64String)
    {
        if (string.IsNullOrEmpty(base64String))
        {
            return null;
        }

        try
        {
            byte[] imageBytes = Convert.FromBase64String(base64String);
            Texture2D tex = new Texture2D(2, 2, TextureFormat.RGBA32, false);

            bool loaded = tex.LoadImage(imageBytes);
            if (!loaded)
            {
                Debug.LogError("Failed to load image bytes into texture.");
                return null;
            }

            return tex;
        }
        catch (Exception e)
        {
            Debug.LogError("Base64 decode failed: " + e.Message);
            return null;
        }
    }

    void SaveTextureIfPossible(Texture2D tex, string fileName)
    {
        if (tex == null)
        {
            Debug.LogWarning("Did not save " + fileName + " because texture is null.");
            return;
        }

        try
        {
            byte[] bytes = tex.EncodeToPNG();
            string path = System.IO.Path.Combine(Application.persistentDataPath, fileName);
            System.IO.File.WriteAllBytes(path, bytes);
            Debug.Log("Saved file to: " + path);
        }
        catch (Exception e)
        {
            Debug.LogWarning("Could not save texture: " + e.Message);
        }
    }
}