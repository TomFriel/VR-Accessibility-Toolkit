// Assets/Scripts/CvdModeDriver.cs
using UnityEngine;

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

    [Header("The EXACT material used in your URP Full Screen Pass Renderer Feature")]
    [SerializeField] private Material passMaterial;

    [Header("Runtime values")]
    [SerializeField] private CvdMode mode = CvdMode.Normal;

    [Range(0f, 1f)]
    [SerializeField] private float strength = 1f;

    [Header("Keyboard (Editor)")]
    [SerializeField] private bool enableKeyboard = true;

    // Shader Graph property names are usually _Mode / _Strength under the hood.
    private static readonly int ModeId = Shader.PropertyToID("_Mode");
    private static readonly int StrengthId = Shader.PropertyToID("_Strength");
    private static readonly int ModeAltId = Shader.PropertyToID("Mode");
    private static readonly int StrengthAltId = Shader.PropertyToID("Strength");

    private void OnEnable()
    {
        ApplyToMaterial();
    }

    private void OnValidate()
    {
        ApplyToMaterial();
    }

    private void Update()
    {
        if (!enableKeyboard) return;

        // In edit mode, Unity still calls Update with ExecuteAlways
        // but Input only works reliably in Play Mode.
        if (!Application.isPlaying) return;

        if (Input.GetKeyDown(KeyCode.Alpha1)) SetMode(CvdMode.Normal);
        if (Input.GetKeyDown(KeyCode.Alpha2)) SetMode(CvdMode.Deuteranopia);
        if (Input.GetKeyDown(KeyCode.Alpha3)) SetMode(CvdMode.Protanopia);
        if (Input.GetKeyDown(KeyCode.Alpha4)) SetMode(CvdMode.Tritanopia);
    }

    public void SetMode(CvdMode newMode)
    {
        mode = newMode;
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

        // Important: set BOTH possible property name styles so it works regardless
        // of how Shader Graph compiled your properties.
        SetFloatSmart(passMaterial, ModeId, ModeAltId, (float)mode);
        SetFloatSmart(passMaterial, StrengthId, StrengthAltId, strength);
    }

    private static void SetFloatSmart(Material mat, int idA, int idB, float value)
    {
        if (mat.HasProperty(idA)) mat.SetFloat(idA, value);
        else if (mat.HasProperty(idB)) mat.SetFloat(idB, value);
    }
}
