using UnityEngine;

/*
PSEUDOCODE (clear overview)
--------------------------
- Make a world-space UI canvas face the player's camera.
- Useful for poster button panels so text/buttons are readable in VR.
*/

public class BillboardUI : MonoBehaviour
{
    [SerializeField] private Camera targetCamera;

    private void Start()
    {
        if (targetCamera == null)
        {
            targetCamera = Camera.main;
        }
    }

    private void LateUpdate()
    {
        if (targetCamera == null) return;

        Vector3 direction = transform.position - targetCamera.transform.position;
        transform.rotation = Quaternion.LookRotation(direction);
    }
}
