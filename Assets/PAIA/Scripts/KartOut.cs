using UnityEngine;

public class KartOut : MonoBehaviour
{
    public LayerMask GroundLayer;

    [SerializeField]
    private PAIAKartAgent agent;

    void OnTriggerEnter(Collider other)
    {
        if ((GroundLayer.value & (1 << other.gameObject.layer)) > 0)
            agent.OutOfBound();
    }
}