using UnityEngine;

public class GenerateOnStart : MonoBehaviour
{
    public PosterGenerationClient client;
    public bool runOnStart = true;

    void Start()
    {
        if (runOnStart && client != null)
        {
            client.GeneratePosterOutputs();
        }
    }
}