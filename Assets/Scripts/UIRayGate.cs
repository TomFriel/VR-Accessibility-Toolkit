using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit.Interactors;

public class UIRayGate : MonoBehaviour
{
    [Header("Right-hand UI ray pieces")]
    [SerializeField] private XRRayInteractor rayInteractor;
    [SerializeField] private LineRenderer lineRenderer;
    [SerializeField] private Behaviour lineVisualBehaviour;
    [SerializeField] private GameObject rayVisualObject;

    [Header("Start state")]
    [SerializeField] private bool visualStartsEnabled = true;

    private void Start()
    {
        SetVisualActive(visualStartsEnabled);
    }

    public void SetVisualActive(bool active)
    {
        if (lineRenderer != null)
            lineRenderer.enabled = active;

        if (lineVisualBehaviour != null)
            lineVisualBehaviour.enabled = active;

        if (rayVisualObject != null)
            rayVisualObject.SetActive(active);
    }

    public void EnableRayVisual()
    {
        SetVisualActive(true);
    }

    public void DisableRayVisual()
    {
        SetVisualActive(false);
    }

    public XRRayInteractor GetRayInteractor()
    {
        return rayInteractor;
    }
}