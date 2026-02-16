using System;
using UnityEngine;

/// <summary>
/// Controls global colour-blind simulation using a URP Full Screen Pass material.
/// This replaces the old Volume ColorAdjustments "fake filter" approach.
/// </summary>
public class ColourBlindModeController : MonoBehaviour
{
    /// <summary>
    /// The supported CVD modes. Matches shader _Mode:
    /// 0 = Normal, 1 = Protanopia, 2 = Deuteranopia, 3 = Tritanopia
    /// </summary>
    public enum CvdMode
    {
        Normal = 0,
        Protanopia = 1,
        Deuteranopia = 2,
        Tritanopia = 3
    }

    /// <summary>
    /// Other scripts can read this without needing a reference.
    /// (Example: posters deciding which fixed material to show.)
    /// </summary>
    public static CvdMode CurrentMode { get; private set; } = CvdMode.Normal;

    [Header("Current CVD Mode")]
    public CvdMode mode = CvdMode.Normal;

    [Header("Fullscreen CVD Material (used by URP Full Screen Pass)")]
    [Tooltip("Drag Mat_CVD_Fullscreen here (material using CVD/ColorBlindrURP_Fullscreen).")]
    public Material cvdFullscreenMaterial;

    [Header("Simulation Strength")]
    [Range(0f, 1f)]
    public float strength = 1f;

    // Shader property IDs (faster + avoids typos)
    private static readonly int ModeId = Shader.PropertyToID("_Mode");
    private static readonly int StrengthId = Shader.PropertyToID("_Strength");

    /// <summary>
    /// Fired when the mode changes so managers (Apply Fix) can update posters immediately.
    /// </summary>
    public event Action<CvdMode> OnModeChanged;

    private void Start()
    {
        // Set initial state
        ApplyMode(forceEvent: true);
    }

    private void Update()
    {
        // TEMP: keyboard input for Editor testing.
        // Later: hook to VR UI button events.
        if (Input.GetKeyDown(KeyCode.Alpha1)) SetMode(CvdMode.Normal);
        else if (Input.GetKeyDown(KeyCode.Alpha2)) SetMode(CvdMode.Protanopia);
        else if (Input.GetKeyDown(KeyCode.Alpha3)) SetMode(CvdMode.Deuteranopia);
        else if (Input.GetKeyDown(KeyCode.Alpha4)) SetMode(CvdMode.Tritanopia);

        // If you tweak strength live in Inspector, keep shader updated
        if (cvdFullscreenMaterial != null)
        {
            cvdFullscreenMaterial.SetFloat(StrengthId, strength);
        }
    }

    public void SetMode(CvdMode newMode)
    {
        if (mode == newMode) return;
        mode = newMode;
        ApplyMode(forceEvent: true);
    }

    /// <summary>
    /// Writes mode/strength to the fullscreen material.
    /// </summary>
    private void ApplyMode(bool forceEvent)
    {
        CurrentMode = mode;

        if (cvdFullscreenMaterial == null)
        {
            Debug.LogWarning("CBC: No cvdFullscreenMaterial assigned. Drag Mat_CVD_Fullscreen onto this script.");
            return;
        }

        cvdFullscreenMaterial.SetFloat(ModeId, (float)mode);
        cvdFullscreenMaterial.SetFloat(StrengthId, strength);

        Debug.Log($"CBC: Mode applied: {mode} (Mode={(float)mode}, Strength={strength})");

        if (forceEvent)
        {
            OnModeChanged?.Invoke(mode);
        }
    }
}
