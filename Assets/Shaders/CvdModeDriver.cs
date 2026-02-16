using UnityEngine;

public class CvdModeDriver : MonoBehaviour
{
    [Header("Material used by the URP Full Screen Pass")]
    public Material fullscreenMat;

    [Header("Runtime values")]
    [Range(0, 10)] public int mode = 0;
    [Range(0f, 1f)] public float strength = 1f;

    // These usually become "_Mode" and "_Strength" in Shader Graph materials.
    // If yours are different, see the note below.
    private static readonly int ModeID = Shader.PropertyToID("_Mode");
    private static readonly int StrengthID = Shader.PropertyToID("_Strength");

    void Start()
    {
        Apply();
    }

    void Update()
    {
        // Example keyboard controls (replace later with XR input / UI)
        if (Input.GetKeyDown(KeyCode.Alpha0)) { mode = 0; Apply(); } // normal
        if (Input.GetKeyDown(KeyCode.Alpha1)) { mode = 1; Apply(); }
        if (Input.GetKeyDown(KeyCode.Alpha2)) { mode = 2; Apply(); }
        if (Input.GetKeyDown(KeyCode.Alpha3)) { mode = 3; Apply(); }
        if (Input.GetKeyDown(KeyCode.Alpha4)) { mode = 4; Apply(); }

        // Strength tweak (optional)
        if (Input.GetKeyDown(KeyCode.Minus)) { strength = Mathf.Clamp01(strength - 0.1f); Apply(); }
        if (Input.GetKeyDown(KeyCode.Equals)) { strength = Mathf.Clamp01(strength + 0.1f); Apply(); }
    }

    public void Apply()
    {
        if (fullscreenMat == null) return;

        fullscreenMat.SetFloat(ModeID, mode);
        fullscreenMat.SetFloat(StrengthID, strength);

        // Helpful log while testing
        Debug.Log($"CVD Apply -> Mode={mode}, Strength={strength}");
    }
}
