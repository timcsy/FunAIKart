using UnityEngine;

public class KartCrash : MonoBehaviour
{
    public LayerMask TrackLayer;
    public LayerMask GroundLayer;

    [SerializeField]
    private PAIAKartAgent agent;

    void OnTriggerEnter(Collider other)
    {
        if ((TrackLayer.value & (1 << other.gameObject.layer)) > 0)
            agent.Crash();
    }

    void OnTriggerStay(Collider other)
    {
        if ((GroundLayer.value & (1 << other.gameObject.layer)) > 0)
            agent.OutOfBound();

        if ((TrackLayer.value & (1 << other.gameObject.layer)) > 0)
            agent.Grinding();
    }
}