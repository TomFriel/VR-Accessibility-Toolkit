using TMPro;
using TMPro.EditorUtilities;
using UnityEngine;
using UnityEngine.UI;

public class TextReadabilityPoster : MonoBehaviour


{
    private Material exampleMaterialInstance;
    private Material instructionMaterialInstance;

    public enum BackgroundType
    {
        Instructions,
        ConflictFlat,
        ConflictTextured,
        MatchColour
    }

    public enum DisplayMode
    {
        Original,
        Fix,
        FixPlus
    }

    [Header("UI References")]
    public Image backgroundImage;
    public TMP_Text instructionText;
    public TMP_Text exampleText;
    public GameObject backingPanel;

    [Header("Background Sprites")]
    public Sprite instructionsBackground;
    public Sprite conflictFlatBackground;
    public Sprite conflictTexturedBackground;
    public Sprite matchColourBackground;

    [Header("Text Colours")]
    public Color originalTextColour = Color.red;
    public Color fixTextColour = Color.white;

    [Header("Current State")]
    public BackgroundType currentBackground = BackgroundType.Instructions;
    public DisplayMode currentMode = DisplayMode.Original;

    private void Start()
    {
        if (exampleText != null)
        {
            exampleMaterialInstance = new Material(exampleText.fontMaterial);
            exampleText.fontMaterial = exampleMaterialInstance;
        }

        if (instructionText != null)
        {
            instructionMaterialInstance = new Material(instructionText.fontMaterial);
            instructionText.fontMaterial = instructionMaterialInstance;
        }

        UpdatePoster();
    }

    public void SetBackgroundInstructions()
    {
        currentBackground = BackgroundType.Instructions;
        UpdatePoster();
    }

    public void SetBackgroundConflictFlat()
    {
        currentBackground = BackgroundType.ConflictFlat;
        UpdatePoster();
    }

    public void SetBackgroundConflictTextured()
    {
        currentBackground = BackgroundType.ConflictTextured;
        UpdatePoster();
    }

    public void SetBackgroundMatchColour()
    {
        currentBackground = BackgroundType.MatchColour;
        UpdatePoster();
    }

    public void SetModeOriginal()
    {
        currentMode = DisplayMode.Original;
        UpdatePoster();
    }

    public void SetModeFix()
    {
        currentMode = DisplayMode.Fix;
        UpdatePoster();
    }

    public void SetModeFixPlus()
    {
        currentMode = DisplayMode.FixPlus;
        UpdatePoster();
    }

    private void UpdatePoster()
    {
        UpdateBackground();
        UpdateVisibleText();
        UpdateTextColours();
        UpdateBackingPanel();
    }

    private void UpdateBackground()
    {
        switch (currentBackground)
        {
            case BackgroundType.Instructions:
                backgroundImage.sprite = instructionsBackground;
                break;

            case BackgroundType.ConflictFlat:
                backgroundImage.sprite = conflictFlatBackground;
                break;

            case BackgroundType.ConflictTextured:
                backgroundImage.sprite = conflictTexturedBackground;
                break;

            case BackgroundType.MatchColour:
                backgroundImage.sprite = matchColourBackground;
                break;
        }
    }

    private void UpdateVisibleText()
    {
        bool showInstructions = currentBackground == BackgroundType.Instructions;

        if (instructionText != null)
            instructionText.gameObject.SetActive(showInstructions);

        if (exampleText != null)
            exampleText.gameObject.SetActive(!showInstructions);
    }

    private void UpdateBackingPanel()
    {
        if (backingPanel == null) return;

        bool showInstructions = currentBackground == BackgroundType.Instructions;

        // Hide backing panel on instructions screen
        if (showInstructions)
        {
            backingPanel.SetActive(false);
        }
        else
        {
            backingPanel.SetActive(currentMode == DisplayMode.FixPlus);
        }
    }

    private void Update()
    {
        // Temporary keyboard debug
        if (Input.GetKeyDown(KeyCode.Alpha6)) SetBackgroundInstructions();
        if (Input.GetKeyDown(KeyCode.Alpha7)) SetBackgroundConflictFlat();
        if (Input.GetKeyDown(KeyCode.Alpha8)) SetBackgroundConflictTextured();
        if (Input.GetKeyDown(KeyCode.Alpha9)) SetBackgroundMatchColour();

        if (Input.GetKeyDown(KeyCode.Q)) SetModeOriginal();
        if (Input.GetKeyDown(KeyCode.W)) SetModeFix();
        if (Input.GetKeyDown(KeyCode.E)) SetModeFixPlus();
    }

    private void UpdateTextColours()
    {
        Color chosenColour = currentMode == DisplayMode.Original
            ? originalTextColour
            : fixTextColour;

        if (instructionText != null)
        {
            instructionText.color = chosenColour;

            if (instructionMaterialInstance != null)
            {
                if (currentMode == DisplayMode.Original)
                {
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_OutlineWidth, 0f);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlaySoftness, 0f);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayDilate, 0f);
                }
                else if (currentMode == DisplayMode.Fix)
                {
                    instructionMaterialInstance.SetColor(ShaderUtilities.ID_OutlineColor, Color.black);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_OutlineWidth, 0.2f);

                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlaySoftness, 0f);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayDilate, 0f);
                }
                else if (currentMode == DisplayMode.FixPlus)
                {
                    instructionMaterialInstance.SetColor(ShaderUtilities.ID_OutlineColor, Color.black);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_OutlineWidth, 0.2f);

                    instructionMaterialInstance.SetColor(ShaderUtilities.ID_UnderlayColor, new Color(0, 0, 0, 0.6f));
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlaySoftness, 0.6f);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayDilate, 0.2f);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayOffsetX, 0f);
                    instructionMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayOffsetY, 0f);
                }
            }
        }

        if (exampleText != null)
        {
            exampleText.color = chosenColour;

            if (exampleMaterialInstance != null)
            {
                if (currentMode == DisplayMode.Original)
                {
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_OutlineWidth, 0f);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlaySoftness, 0f);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayDilate, 0f);
                }
                else if (currentMode == DisplayMode.Fix)
                {
                    exampleMaterialInstance.SetColor(ShaderUtilities.ID_OutlineColor, Color.black);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_OutlineWidth, 0.2f);

                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlaySoftness, 0f);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayDilate, 0f);
                }
                else if (currentMode == DisplayMode.FixPlus)
                {
                    exampleMaterialInstance.SetColor(ShaderUtilities.ID_OutlineColor, Color.black);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_OutlineWidth, 0.2f);

                    exampleMaterialInstance.SetColor(ShaderUtilities.ID_UnderlayColor, new Color(0, 0, 0, 0.6f));
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlaySoftness, 0.6f);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayDilate, 0.2f);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayOffsetX, 0f);
                    exampleMaterialInstance.SetFloat(ShaderUtilities.ID_UnderlayOffsetY, 0f);
                }
            }
        }
    }
}