using UnityEngine;

public class KartCrash : MonoBehaviour
{
    public LayerMask TrackLayer;

    [SerializeField]
    private PAIAKartAgent agent;

    void OnTriggerEnter(Collider other)
    {
        if ((TrackLayer.value & (1 << other.gameObject.layer)) > 0)
            agent.Crash();
    }

    void OnTriggerStay(Collider other)
    {
        if ((TrackLayer.value & (1 << other.gameObject.layer)) > 0)
            agent.Grinding();
    }
}