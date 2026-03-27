using UnityEngine;
using UnityEngine.InputSystem;

public class WristMenuToggle : MonoBehaviour
{
    [Header("Menu")]
    [SerializeField] private GameObject wristMenu;

    [Header("Optional Ray Control")]
    [SerializeField] private bool controlRayWithMenu = true;
    [SerializeField] private UIRayGate uiRayGate;

    [Header("Input")]
    [SerializeField] private InputActionReference toggleMenuAction;

    [Header("Settings")]
    [SerializeField] private bool startOpen = false;
    [SerializeField] private bool autoCloseAfterModeSelect = false;

    private bool isOpen;

    private void OnEnable()
    {
        if (toggleMenuAction != null && toggleMenuAction.action != null)
        {
            toggleMenuAction.action.Enable();
            toggleMenuAction.action.performed += OnTogglePressed;
        }
    }

    private void OnDisable()
    {
        if (toggleMenuAction != null && toggleMenuAction.action != null)
        {
            toggleMenuAction.action.performed -= OnTogglePressed;
            toggleMenuAction.action.Disable();
        }
    }

    private void Start()
    {
        SetMenuState(startOpen);
    }

    private void OnTogglePressed(InputAction.CallbackContext context)
    {
        SetMenuState(!isOpen);
    }

    public void SetMenuState(bool open)
    {
        isOpen = open;

        if (wristMenu != null)
            wristMenu.SetActive(isOpen);

        if (controlRayWithMenu && uiRayGate != null)
        {
            if (isOpen) uiRayGate.EnableRayVisual();
            else uiRayGate.DisableRayVisual();
        }
    }

    public void CloseMenu()
    {
        SetMenuState(false);
    }

    public void OpenMenu()
    {
        SetMenuState(true);
    }

    public void OnModeChosen()
    {
        if (autoCloseAfterModeSelect)
            CloseMenu();
    }
}