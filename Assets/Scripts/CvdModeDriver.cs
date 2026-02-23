﻿// Assets/Scripts/CvdModeDriver.cs
using UnityEngine;

/*
PSEUDOCODE
--------------------------
- Store the active CVD mode (Normal / Deuteranopia / Protanopia / Tritanopia).
- Store an effect strength value (0..1).
- Push mode + strength into the URP Full Screen Pass material used by the post-process shader.
- In Play Mode, allow number keys 1–4 to switch modes (optional toggle).
- Provide a static Instance so other scripts can read the current mode/strength.
*/

[ExecuteAlways] // Runs in editor + play mode so inspector changes can update the material immediately.
public class CvdModeDriver : MonoBehaviour
{
    // Supported CVD modes (numeric mapping is used by the shader).
    public enum CvdMode
    {
        Normal = 0,
        Deuteranopia = 1,
        Protanopia = 2,
        Tritanopia = 3
    }

    // Singleton-style access for other scripts.
    public static CvdModeDriver Instance { get; private set; }
    public CvdMode CurrentMode => mode;       // Current mode getter.
    public float CurrentStrength => strength; // Current strength getter.

    [Header("The EXACT material used in your URP Full Screen Pass Renderer Feature")]
    [SerializeField] private Material passMaterial; // Material assigned to the URP Full Screen Pass feature.

    [Header("Runtime values")]
    [SerializeField] private CvdMode mode = CvdMode.Normal; // Active CVD mode.

    [Range(0f, 1f)]
    [SerializeField] private float strength = 1f; // Effect strength (0..1).

    [Header("Keyboard (Editor)")]
    [SerializeField] private bool enableKeyboard = true; // Enables key controls in Play Mode.

    // Shader property IDs for fast lookup (supports both "_Name" and "Name" variants).
    private static readonly int ModeId = Shader.PropertyToID("_Mode");
    private static readonly int StrengthId = Shader.PropertyToID("_Strength");
    private static readonly int ModeAltId = Shader.PropertyToID("Mode");
    private static readonly int StrengthAltId = Shader.PropertyToID("Strength");

    private void OnEnable() // Registers Instance and applies current values to the material.
    {
        Instance = this;
        ApplyToMaterial();
    }

    private void OnDisable() // Clears Instance if this object was the active driver.
    {
        if (Instance == this) Instance = null;
    }

    private void OnValidate() // Re-applies material parameters when inspector values change.
    {
        ApplyToMaterial();
    }

    private void Update() // Handles key input (1–4) during Play Mode to change CVD mode.
    {
        if (!enableKeyboard) return;           // Stops if keyboard control is disabled.
        if (!Application.isPlaying) return;    // Prevents edit-mode key handling (ExecuteAlways runs Update in editor).

        if (Input.GetKeyDown(KeyCode.Alpha1)) SetMode(CvdMode.Normal);
        if (Input.GetKeyDown(KeyCode.Alpha2)) SetMode(CvdMode.Deuteranopia);
        if (Input.GetKeyDown(KeyCode.Alpha3)) SetMode(CvdMode.Protanopia);
        if (Input.GetKeyDown(KeyCode.Alpha4)) SetMode(CvdMode.Tritanopia);
    }

    public void SetMode(CvdMode newMode) // Sets the active mode and updates the material.
    {
        mode = newMode;
        ApplyToMaterial();
    }

    public void SetStrength(float newStrength) // Clamps strength to 0..1 and updates the material.
    {
        strength = Mathf.Clamp01(newStrength);
        ApplyToMaterial();
    }

    private void ApplyToMaterial() // Writes mode + strength values into the fullscreen pass material.
    {
        if (passMaterial == null) return; // No-op if the material reference is missing.

        // Sets properties using whichever name exists in the shader/material.
        SetFloatSmart(passMaterial, ModeId, ModeAltId, (float)mode);
        SetFloatSmart(passMaterial, StrengthId, StrengthAltId, strength);
    }

    private static void SetFloatSmart(Material mat, int idA, int idB, float value) // Sets the first existing shader property.
    {
        if (mat.HasProperty(idA)) mat.SetFloat(idA, value);
        else if (mat.HasProperty(idB)) mat.SetFloat(idB, value);
    }
}
