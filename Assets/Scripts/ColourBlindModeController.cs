using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public class ColourBlindModeController : MonoBehaviour
{
    private Volume volume;
    private ColorAdjustments colorAdjustments;

    public enum CvdMode
    {
        Normal = 0,
        Desaturate = 1,
        BlueTint = 2
    }

    public CvdMode mode = CvdMode.Normal;

    void Start()
    {
        // Try to get a Volume on THIS object first
        volume = GetComponent<Volume>();

        // If this object doesn't have one, just grab ANY Volume in the scene
        if (volume == null)
        {
            volume = FindObjectOfType<Volume>();
        }

        if (volume == null)
        {
            Debug.LogError("ColourBlindModeController: No Volume found in the scene.");
            return;
        }

        if (!volume.profile.TryGet(out colorAdjustments))
        {
            Debug.LogError("ColourBlindModeController: No ColorAdjustments override found on the Volume profile.");
            return;
        }

        ApplyMode();
    }

    void Update()
    {
        // Keyboard test controls for now
        if (Input.GetKeyDown(KeyCode.Alpha1))
        {
            mode = CvdMode.Normal;
            ApplyMode();
        }
        else if (Input.GetKeyDown(KeyCode.Alpha2))
        {
            mode = CvdMode.Desaturate;
            ApplyMode();
        }
        else if (Input.GetKeyDown(KeyCode.Alpha3))
        {
            mode = CvdMode.BlueTint;
            ApplyMode();
        }
    }

    private void ApplyMode()
    {
        if (colorAdjustments == null) return;

        switch (mode)
        {
            case CvdMode.Normal:
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = 0f;
                colorAdjustments.colorFilter.value = Color.white;
                break;

            case CvdMode.Desaturate:
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -80f;
                colorAdjustments.colorFilter.value = Color.white;
                break;

            case CvdMode.BlueTint:
                colorAdjustments.postExposure.value = 0f;
                colorAdjustments.contrast.value = 0f;
                colorAdjustments.saturation.value = -20f;
                colorAdjustments.colorFilter.value = new Color(0.8f, 0.9f, 1f);
                break;
        }
    }
}
