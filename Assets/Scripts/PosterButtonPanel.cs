using UnityEngine;

/*
PSEUDOCODE (clear overview)
--------------------------
- This script sits on the world-space canvas above a poster.
- It holds a reference to one AccessibilityPoster.
- Each UI button calls one public method:
    - ShowOriginal()
    - ShowFix()
    - ShowFixPlus()
- These buttons affect ONLY that poster.
*/

public class PosterButtonPanel : MonoBehaviour
{
    [SerializeField] private AccessibilityPoster targetPoster;

    public void SetPoster(AccessibilityPoster poster)
    {
        targetPoster = poster;
    }

    public void ShowOriginal()
    {
        if (targetPoster != null)
        {
            targetPoster.ShowOriginal();
        }
    }

    public void ShowFix()
    {
        if (targetPoster != null)
        {
            targetPoster.ShowFix();
        }
    }

    public void ShowFixPlus()
    {
        if (targetPoster != null)
        {
            targetPoster.ShowFixPlus();
        }
    }
}
