using UnityEngine;

public class ModeButtonClick : MonoBehaviour
{
    [SerializeField] private WristMenuToggle wristMenuToggle;

    public void NotifyModeChosen()
    {
        if (wristMenuToggle != null)
        {
            wristMenuToggle.OnModeChosen();
        }
    }
}