using UnityEngine;

/*
PSEUDOCODE
--------------------------
- Store the active CVD mode (Normal / Deuteranopia / Protanopia / Tritanopia).
- Store an effect strength value (0..1).
- Push mode + strength into the URP Full Screen Pass material used by the post-process shader.
- In Play Mode, allow number keys 1–4 to switch modes (optional toggle).
- Provide public button-friendly methods so VR UI buttons can call them directly.
- Provide a static Instance so other scripts can read the current mode/strength.
*/

// Manages color vision deficiency mode and applies it to the post-process material.
[ExecuteAlways]
public class CvdModeDriver : MonoBehaviour
{
    // CVD modes supported by the system.
    public enum CvdMode
    {
        Normal = 0,
        Deuteranopia = 1,
        Protanopia = 2,
        Tritanopia = 3
    }

    // Global instance for external access.
    public static CvdModeDriver Instance { get; private set; }
    // Current CVD mode.
    public CvdMode CurrentMode => mode;
    // Current effect strength (0-1).
    public float CurrentStrength => strength;

    // URP Full Screen Pass material for post-process shader.
    [Header("The EXACT material used in your URP Full Screen Pass Renderer Feature")]
    [SerializeField] private Material passMaterial;

    // Current CVD mode.
    [Header("Runtime values")]
    [SerializeField] private CvdMode mode = CvdMode.Normal;

    // Effect strength (0 = off, 1 = full).
    [Range(0f, 1f)]
    [SerializeField] private float strength = 1f;

    // Enable keyboard shortcuts in editor.
    [Header("Keyboard (Editor)")]
    [SerializeField] private bool enableKeyboard = true;

    // Shader property IDs for material parameters.
    private static readonly int ModeId = Shader.PropertyToID("_Mode");
    private static readonly int StrengthId = Shader.PropertyToID("_Strength");
    // Fallback property IDs without underscore prefix.
    private static readonly int ModeAltId = Shader.PropertyToID("Mode");
    private static readonly int StrengthAltId = Shader.PropertyToID("Strength");

    // Register instance and apply current settings to material.
    private void OnEnable()
    {
        Instance = this;
        ApplyToMaterial();
    }

    // Clear instance reference on disable.
    private void OnDisable()
    {
        if (Instance == this) Instance = null;
    }

    // Update material when values change in inspector.
    private void OnValidate()
    {
        ApplyToMaterial();
    }

    // Handle keyboard input (number keys 1-4 to switch modes).
    private void Update()
    {
        if (!enableKeyboard) return;
        if (!Application.isPlaying) return;

        // Key 1 = Normal
        if (Input.GetKeyDown(KeyCode.Alpha1)) SetNormal();
        // Key 2 = Deuteranopia
        if (Input.GetKeyDown(KeyCode.Alpha2)) SetDeuteranopia();
        // Key 3 = Protanopia
        if (Input.GetKeyDown(KeyCode.Alpha3)) SetProtanopia();
        // Key 4 = Tritanopia
        if (Input.GetKeyDown(KeyCode.Alpha4)) SetTritanopia();
    }

    // Switch to Normal mode.
    public void SetNormal()
    {
        SetMode(CvdMode.Normal);
    }

    // Switch to Deuteranopia mode.
    public void SetDeuteranopia()
    {
        SetMode(CvdMode.Deuteranopia);
    }

    // Switch to Protanopia mode.
    public void SetProtanopia()
    {
        SetMode(CvdMode.Protanopia);
    }

    // Switch to Tritanopia mode.
    public void SetTritanopia()
    {
        SetMode(CvdMode.Tritanopia);
    }

    // Set mode by enum and update material.
    public void SetMode(CvdMode newMode)
    {
        mode = newMode;
        ApplyToMaterial();
    }

    // Set mode by integer (0-3) and update material.
    public void SetMode(int newMode)
    {
        newMode = Mathf.Clamp(newMode, 0, 3);
        mode = (CvdMode)newMode;
        ApplyToMaterial();
    }

    // Set effect strength (0-1) and update material.
    public void SetStrength(float newStrength)
    {
        strength = Mathf.Clamp01(newStrength);
        ApplyToMaterial();
    }

    // Apply current mode and strength to material properties.
    private void ApplyToMaterial()
    {
        if (passMaterial == null) return;

        // Set mode property
        SetFloatSmart(passMaterial, ModeId, ModeAltId, (float)mode);
        // Set strength property
        SetFloatSmart(passMaterial, StrengthId, StrengthAltId, strength);
    }

    // Set material float property using primary ID, fallback to alternate ID if not found.
    private static void SetFloatSmart(Material mat, int idA, int idB, float value)
    {
        if (mat.HasProperty(idA)) mat.SetFloat(idA, value);
        else if (mat.HasProperty(idB)) mat.SetFloat(idB, value);
    }
}
