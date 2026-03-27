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

[ExecuteAlways]
public class CvdModeDriver : MonoBehaviour
{
    public enum CvdMode
    {
        Normal = 0,
        Deuteranopia = 1,
        Protanopia = 2,
        Tritanopia = 3
    }

    public static CvdModeDriver Instance { get; private set; }
    public CvdMode CurrentMode => mode;
    public float CurrentStrength => strength;

    [Header("The EXACT material used in your URP Full Screen Pass Renderer Feature")]
    [SerializeField] private Material passMaterial;

    [Header("Runtime values")]
    [SerializeField] private CvdMode mode = CvdMode.Normal;

    [Range(0f, 1f)]
    [SerializeField] private float strength = 1f;

    [Header("Keyboard (Editor)")]
    [SerializeField] private bool enableKeyboard = true;

    private static readonly int ModeId = Shader.PropertyToID("_Mode");
    private static readonly int StrengthId = Shader.PropertyToID("_Strength");
    private static readonly int ModeAltId = Shader.PropertyToID("Mode");
    private static readonly int StrengthAltId = Shader.PropertyToID("Strength");

    private void OnEnable()
    {
        Instance = this;
        ApplyToMaterial();
    }

    private void OnDisable()
    {
        if (Instance == this) Instance = null;
    }

    private void OnValidate()
    {
        ApplyToMaterial();
    }

    private void Update()
    {
        if (!enableKeyboard) return;
        if (!Application.isPlaying) return;

        if (Input.GetKeyDown(KeyCode.Alpha1)) SetNormal();
        if (Input.GetKeyDown(KeyCode.Alpha2)) SetDeuteranopia();
        if (Input.GetKeyDown(KeyCode.Alpha3)) SetProtanopia();
        if (Input.GetKeyDown(KeyCode.Alpha4)) SetTritanopia();
    }

    public void SetNormal()
    {
        SetMode(CvdMode.Normal);
    }

    public void SetDeuteranopia()
    {
        SetMode(CvdMode.Deuteranopia);
    }

    public void SetProtanopia()
    {
        SetMode(CvdMode.Protanopia);
    }

    public void SetTritanopia()
    {
        SetMode(CvdMode.Tritanopia);
    }

    public void SetMode(CvdMode newMode)
    {
        mode = newMode;
        ApplyToMaterial();
    }

    public void SetMode(int newMode)
    {
        newMode = Mathf.Clamp(newMode, 0, 3);
        mode = (CvdMode)newMode;
        ApplyToMaterial();
    }

    public void SetStrength(float newStrength)
    {
        strength = Mathf.Clamp01(newStrength);
        ApplyToMaterial();
    }

    private void ApplyToMaterial()
    {
        if (passMaterial == null) return;

        SetFloatSmart(passMaterial, ModeId, ModeAltId, (float)mode);
        SetFloatSmart(passMaterial, StrengthId, StrengthAltId, strength);
    }

    private static void SetFloatSmart(Material mat, int idA, int idB, float value)
    {
        if (mat.HasProperty(idA)) mat.SetFloat(idA, value);
        else if (mat.HasProperty(idB)) mat.SetFloat(idB, value);
    }
}
