using UnityEngine;
using UnityEngine.XR;

public class DisableOcclusionMesh : MonoBehaviour
{
    void Start()
    {
        XRSettings.useOcclusionMesh = false;
        Debug.Log("DisableOcclusionMesh: Occlusion mesh disabled.");
    }
}
