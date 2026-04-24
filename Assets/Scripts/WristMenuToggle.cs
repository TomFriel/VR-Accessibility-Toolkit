using UnityEngine;
using UnityEngine.InputSystem;

// Manages visibility and interaction of the wrist menu in VR.
public class WristMenuToggle : MonoBehaviour
{
    // The wrist menu GameObject to toggle.
    [Header("Menu")]
    [SerializeField] private GameObject wristMenu;

    // Enable/disable UI ray based on menu state.
    [Header("Optional Ray Control")]
    [SerializeField] private bool controlRayWithMenu = true;
    // Reference to UI ray gate for enabling/disabling ray visual.
    [SerializeField] private UIRayGate uiRayGate;

    // Input action for toggling menu open/close.
    [Header("Input")]
    [SerializeField] private InputActionReference toggleMenuAction;

    // Open menu on start.
    [Header("Settings")]
    [SerializeField] private bool startOpen = false;
    // Close menu automatically after mode selection.
    [SerializeField] private bool autoCloseAfterModeSelect = false;

    // Current menu open/close state.
    private bool isOpen;

    // Register input action callbacks.
    private void OnEnable()
    {
        if (toggleMenuAction != null && toggleMenuAction.action != null)
        {
            toggleMenuAction.action.Enable();
            toggleMenuAction.action.performed += OnTogglePressed;
        }
    }

    // Unregister input action callbacks.
    private void OnDisable()
    {
        if (toggleMenuAction != null && toggleMenuAction.action != null)
        {
            toggleMenuAction.action.performed -= OnTogglePressed;
            toggleMenuAction.action.Disable();
        }
    }

    // Initialize menu state based on settings.
    private void Start()
    {
        SetMenuState(startOpen);
    }

    // Toggle menu state when input action is performed.
    private void OnTogglePressed(InputAction.CallbackContext context)
    {
        SetMenuState(!isOpen);
    }

    // Set menu visibility and optionally control UI ray.
    public void SetMenuState(bool open)
    {
        isOpen = open;

        // Activate or deactivate the menu GameObject
        if (wristMenu != null)
            wristMenu.SetActive(isOpen);

        // Show/hide UI ray based on menu state
        if (controlRayWithMenu && uiRayGate != null)
        {
            if (isOpen) uiRayGate.EnableRayVisual();
            else uiRayGate.DisableRayVisual();
        }
    }

    // Close the wrist menu.
    public void CloseMenu()
    {
        SetMenuState(false);
    }

    // Open the wrist menu.
    public void OpenMenu()
    {
        SetMenuState(true);
    }

    // Handle CVD mode selection - optionally close menu.
    public void OnModeChosen()
    {
        if (autoCloseAfterModeSelect)
            CloseMenu();
    }
}