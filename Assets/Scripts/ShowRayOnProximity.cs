using UnityEngine;

public class ShowRayOnProximity : MonoBehaviour
{
    [SerializeField] private UIRayGate uiRayGate;
    [SerializeField] private string requiredTag = "PlayerHand";

    private void OnTriggerEnter(Collider other)
    {
        if (!string.IsNullOrEmpty(requiredTag) && !other.CompareTag(requiredTag))
            return;

        if (uiRayGate != null)
            uiRayGate.EnableRayVisual();
    }

    private void OnTriggerExit(Collider other)
    {
        if (!string.IsNullOrEmpty(requiredTag) && !other.CompareTag(requiredTag))
            return;

        if (uiRayGate != null)
            uiRayGate.DisableRayVisual();
    }
}