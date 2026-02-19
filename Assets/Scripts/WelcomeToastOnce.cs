using UnityEngine;
using TMPro;

public class WelcomeToastOnce : MonoBehaviour
{
    // Other UI scripts can check this to know when welcome is gone
    public static bool WelcomeDismissed { get; private set; } = false;

    [Header("UI References")]
    public TextMeshProUGUI label;
    public CanvasGroup canvasGroup;

    [Header("Message")]
    [TextArea(2, 10)]
    public string message =
        "Welcome to the VR Accessibility Gallery!\n\n" +
        "Use 1–4 to change CVD simulation.\n" +
        "Press G to toggle Apply Fix.\n\n" +
        "Look at the posters and compare readability.";

    [Header("Dismiss (keyboard for testing)")]
    public KeyCode dismissKey = KeyCode.Return;
    public bool allowSpaceToo = true;

    [Header("Dismiss behavior")]
    public bool fadeOnDismiss = true;
    public float fadeSeconds = 0.35f;

    [Header("Show only once ever (PlayerPrefs)")]
    public bool onlyOnceEver = false;              // You can turn this on later for builds
    public string playerPrefsKey = "WelcomeToastShown";

    private bool dismissed = false;
    private bool fading = false;
    private float fadeTimer = 0f;

    void Awake()
    {
        // By default, block other toasts until we dismiss (unless we skip)
        WelcomeDismissed = false;

        if (canvasGroup == null) canvasGroup = GetComponent<CanvasGroup>();
        if (label == null) label = GetComponentInChildren<TextMeshProUGUI>(true);

        // If "only once ever" is enabled and we've shown before, skip instantly
        if (onlyOnceEver && PlayerPrefs.GetInt(playerPrefsKey, 0) == 1)
        {
            WelcomeDismissed = true;
            HideInstant();
            dismissed = true;
            return;
        }

        // Show
        Show(message);

        // Mark shown for next time (only if enabled)
        if (onlyOnceEver)
        {
            PlayerPrefs.SetInt(playerPrefsKey, 1);
            PlayerPrefs.Save();
        }
    }

    void Update()
    {
        if (dismissed) return;

        // Keyboard dismiss for testing in editor
        bool pressed =
            Input.GetKeyDown(dismissKey) ||
            (allowSpaceToo && Input.GetKeyDown(KeyCode.Space));

        if (pressed)
        {
            StartDismiss();
        }

        // Fade logic
        if (fading)
        {
            fadeTimer -= Time.deltaTime;
            float t = (fadeSeconds <= 0f) ? 0f : Mathf.Clamp01(fadeTimer / fadeSeconds);

            if (canvasGroup != null) canvasGroup.alpha = t;

            if (fadeTimer <= 0f)
            {
                FinishDismiss();
            }
        }
    }

    // IMPORTANT: This is what you call from the Button OnClick in VR
    public void DismissWelcome()
    {
        if (dismissed) return;
        StartDismiss();
    }

    private void StartDismiss()
    {
        if (fadeOnDismiss && canvasGroup != null && fadeSeconds > 0f)
        {
            fading = true;
            fadeTimer = fadeSeconds;
        }
        else
        {
            FinishDismiss();
        }
    }

    // Public so it will appear in the Unity OnClick dropdown if you prefer calling it directly
    public void FinishDismiss()
    {
        if (dismissed) return;

        WelcomeDismissed = true;
        dismissed = true;
        fading = false;

        HideInstant();
    }

    public void Show(string text)
    {
        if (label != null) label.text = text;
        if (canvasGroup != null) canvasGroup.alpha = 1f;
        gameObject.SetActive(true);
    }

    private void HideInstant()
    {
        if (canvasGroup != null) canvasGroup.alpha = 0f;
        gameObject.SetActive(false);
    }

    [ContextMenu("Reset Welcome Toast (Show Again)")]
    public void ResetWelcomeToast()
    {
        PlayerPrefs.DeleteKey(playerPrefsKey);
        PlayerPrefs.Save();
    }
}
