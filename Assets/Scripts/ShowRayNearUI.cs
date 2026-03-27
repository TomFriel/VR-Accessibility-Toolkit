using UnityEngine;

public class ShowRayNearUI : MonoBehaviour
{
    [SerializeField] private UIRayGate uiRayGate;

    private int insideCount = 0;

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("PlayerHand") && !other.CompareTag("MainCamera"))
            return;

        insideCount++;
        if (uiRayGate != null)
            uiRayGate.EnableRayVisual();
    }

    private void OnTriggerExit(Collider other)
    {
        if (!other.CompareTag("PlayerHand") && !other.CompareTag("MainCamera"))
            return;

        insideCount = Mathf.Max(insideCount - 1, 0);

        if (insideCount == 0 && uiRayGate != null)
            uiRayGate.DisableRayVisual();
    }
}