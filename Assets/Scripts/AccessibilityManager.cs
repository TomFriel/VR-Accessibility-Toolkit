using UnityEngine;

public class AccessibilityManager : MonoBehaviour
{
    public bool applyFix = false;
    public KeyCode toggleKey = KeyCode.F;

    private AccessibilityPoster[] posters;

    void Start()
    {
        // NEW API (Unity 2022+): use FindObjectsByType instead of FindObjectsOfType
        posters = Object.FindObjectsByType<AccessibilityPoster>(
            FindObjectsSortMode.None // we don't care about sort order
        );

        UpdatePosters();
    }

    void Update()
    {
        if (Input.GetKeyDown(toggleKey))
        {
            applyFix = !applyFix;
            UpdatePosters();
            Debug.Log("ApplyFix set to: " + applyFix);
        }
    }

    private void UpdatePosters()
    {
        if (posters == null) return;

        foreach (var poster in posters)
        {
            if (poster != null)
            {
                poster.ApplyFix(applyFix);
            }
        }
    }
}
