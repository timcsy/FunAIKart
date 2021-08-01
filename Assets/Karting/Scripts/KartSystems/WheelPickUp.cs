using UnityEngine;
using KartGame.KartSystems;

public class WheelPickUp : MonoBehaviour
{
    public void OnTriggerEnter(Collider other)
    {
        if (other.transform.parent.TryGetComponent<ArcadeKart>(out ArcadeKart kart))
        {
            kart.PickUpWheel();
            Destroy(gameObject);
        }
    }
}