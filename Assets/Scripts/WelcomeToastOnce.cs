using UnityEngine;
using TMPro;

/*
PSEUDOCODE (clear overview)
--------------------------
- Show a welcome popup on the VR HUD (World Space Canvas) with a TextMeshPro label.
- Allow dismissal via keyboard (Enter/Space) for quick testing.
- Allow dismissal via UI Button OnClick by calling DismissWelcome()/FinishDismiss().
- Optionally fade out the popup before disabling it.
- Track whether the welcome has been dismissed using a static flag so other toasts can wait.
- Optionally persist "shown once" using PlayerPrefs so it does not reappear in a build.
*/

public class WelcomeToastOnce : MonoBehaviour
{
    // Gate flag for other UI scripts (true only after the welcome is dismissed).
    public static bool WelcomeDismissed { get; private set; } = false;

    [Header("UI References")]
    public TextMeshProUGUI label;           // Text element that displays the welcome message.
    public CanvasGroup canvasGroup;         // CanvasGroup used for fade/visibility control.

    [Header("Message")]
    [TextArea(2, 10)]
    public string message =
        "Welcome to the VR Accessibility Gallery!\n\n" +
        "Use 1–4 to change CVD simulation.\n" +
        "Press G to toggle Apply Fix.\n\n" +
        "Look at the posters and compare readability.";

    [Header("Dismiss (keyboard for testing)")]
    public KeyCode dismissKey = KeyCode.Return; // Key to dismiss the popup while testing in editor.
    public bool allowSpaceToo = true;           // Enables Space as an additional dismiss key.

    [Header("Dismiss behavior")]
    public bool fadeOnDismiss = true;     // Enables fading before the popup is disabled.
    public float fadeSeconds = 0.35f;    // Duration of the fade-out.

    [Header("Show only once ever (PlayerPrefs)")]
    public bool onlyOnceEver = false;                   // If enabled, the popup shows once per machine/user.
    public string playerPrefsKey = "WelcomeToastShown"; // PlayerPrefs key used to remember the popup state.

    private bool dismissed = false;  // Tracks whether the popup has already been dismissed.
    private bool fading = false;     // Tracks whether a fade-out is in progress.
    private float fadeTimer = 0f;    // Countdown timer used for fading.

    void Awake() // Initializes state, optionally skips if already shown, otherwise shows the welcome popup.
    {
        // Default state: other toasts remain blocked until the welcome is dismissed (unless skipped below).
        WelcomeDismissed = false;

        // Auto-fill references if they were not assigned in the Inspector.
        if (canvasGroup == null) canvasGroup = GetComponent<CanvasGroup>();
        if (label == null) label = GetComponentInChildren<TextMeshProUGUI>(true);

        // Skip instantly if configured to show only once and the flag is already set.
        if (onlyOnceEver && PlayerPrefs.GetInt(playerPrefsKey, 0) == 1)
        {
            WelcomeDismissed = true;
            HideInstant();
            dismissed = true;
            return;
        }

        // Show the popup immediately.
        Show(message);

        // Persist "shown once" state if enabled.
        if (onlyOnceEver)
        {
            PlayerPrefs.SetInt(playerPrefsKey, 1);
            PlayerPrefs.Save();
        }
    }

    void Update() // Handles keyboard dismissal and performs fade-out over time (if enabled).
    {
        if (dismissed) return;

        // Keyboard dismissal path (useful for editor testing).
        bool pressed =
            Input.GetKeyDown(dismissKey) ||
            (allowSpaceToo && Input.GetKeyDown(KeyCode.Space));

        if (pressed)
        {
            StartDismiss();
        }

        // Fade-out animation path.
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

    public void DismissWelcome() // Public UI hook for Button OnClick: begins dismissal (fade or instant).
    {
        if (dismissed) return;
        StartDismiss();
    }

    private void StartDismiss() // Starts a fade-out if enabled; otherwise dismisses immediately.
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

    public void FinishDismiss() // Finalizes dismissal: unlocks other toasts and disables the popup.
    {
        if (dismissed) return;

        WelcomeDismissed = true;
        dismissed = true;
        fading = false;

        HideInstant();
    }

    public void Show(string text) // Updates the label text and makes the popup visible.
    {
        if (label != null) label.text = text;
        if (canvasGroup != null) canvasGroup.alpha = 1f;
        gameObject.SetActive(true);
    }

    private void HideInstant() // Immediately hides and disables the popup object.
    {
        if (canvasGroup != null) canvasGroup.alpha = 0f;
        gameObject.SetActive(false);
    }

    [ContextMenu("Reset Welcome Toast (Show Again)")]
    public void ResetWelcomeToast() // Clears PlayerPrefs state so the welcome can be tested again.
    {
        PlayerPrefs.DeleteKey(playerPrefsKey);
        PlayerPrefs.Save();
    }
}
