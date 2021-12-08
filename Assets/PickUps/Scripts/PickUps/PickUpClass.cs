using UnityEngine;
using KartGame.KartSystems;

public class PickUpClass : MonoBehaviour
{
    private float delta = 0.15f;
    private float i = 10;

    private void Update()
    {
        // slightly move the pickup object
        transform.Rotate(new Vector3(0, 50.0f * Time.deltaTime, 0));
        transform.Translate(Vector3.up * delta * Time.deltaTime);
        i -= Time.deltaTime * 5.0f;

        if (i < 0)
        {
            i = 10;
            delta *= -1;
        }
    }

    public void OnTriggerEnter(Collider other)
    {
        if (other.transform.parent.TryGetComponent(out PAIAKartAgent kart))
        {
            PickUpEffect(kart);
            Destroy(gameObject);
        }
    }

    public virtual void PickUpEffect(PAIAKartAgent kart)
    {
        // Implement This in Child Class
        // PickUpManager.instance.PickUp(PickUpType.PickupTypeName, kart);
    }
}