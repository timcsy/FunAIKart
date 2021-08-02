using UnityEngine;
using KartGame.KartSystems;

public class WheelPickUp : MonoBehaviour
{
    private void Update()
    {
        transform.Rotate(new Vector3(0, 50.0f * Time.deltaTime, 0));
    }

    public void OnTriggerEnter(Collider other)
    {
        if (other.transform.parent.TryGetComponent(out ArcadeKart kart))
        {
            kart.PickUpConsumable(ArcadeKart.Consumable.Wheel);
            Destroy(gameObject);
        }
    }
}