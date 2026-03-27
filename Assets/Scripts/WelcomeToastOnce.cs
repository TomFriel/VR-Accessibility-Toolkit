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
    public static bool WelcomeDismissed { get; private set; } = false;

    [Header("UI References")]
    public TextMeshProUGUI label;
    public CanvasGroup canvasGroup;

    [Header("Message")]
    [TextArea(2, 10)]
    public string message =
        "Welcome to the VR Accessibility Gallery!\n\n" +
        "Use the LEFT WRIST MENU to change CVD simulation.\n" +
        "Use the BUTTONS ABOVE EACH POSTER to switch between Original, Fix, and Fix+.\n\n" +
        "Compare how each design reads under different vision conditions.";

    [Header("Dismiss (keyboard for testing)")]
    public KeyCode dismissKey = KeyCode.Return;
    public bool allowSpaceToo = true;

    [Header("Dismiss behavior")]
    public bool fadeOnDismiss = true;
    public float fadeSeconds = 0.35f;

    [Header("Show only once ever (PlayerPrefs)")]
    public bool onlyOnceEver = false;
    public string playerPrefsKey = "WelcomeToastShown";

    private bool dismissed = false;
    private bool fading = false;
    private float fadeTimer = 0f;

    void Awake()
    {
        WelcomeDismissed = false;

        if (canvasGroup == null) canvasGroup = GetComponent<CanvasGroup>();
        if (label == null) label = GetComponentInChildren<TextMeshProUGUI>(true);

        if (onlyOnceEver && PlayerPrefs.GetInt(playerPrefsKey, 0) == 1)
        {
            WelcomeDismissed = true;
            HideInstant();
            dismissed = true;
            return;
        }

        Show(message);

        if (onlyOnceEver)
        {
            PlayerPrefs.SetInt(playerPrefsKey, 1);
            PlayerPrefs.Save();
        }
    }

    void Update()
    {
        if (dismissed) return;

        bool pressed =
            Input.GetKeyDown(dismissKey) ||
            (allowSpaceToo && Input.GetKeyDown(KeyCode.Space));

        if (pressed)
        {
            StartDismiss();
        }

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
