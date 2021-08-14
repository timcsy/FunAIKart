using UnityEngine;
using KartGame.KartSystems;

public class PickUpClass : MonoBehaviour
{
    private float delta = 0.5f;
    private float i = 150;

    private void Update()
    {
        transform.Rotate(new Vector3(0, 50.0f * Time.deltaTime, 0));
        transform.Translate(Vector3.up * delta * Time.deltaTime);
        i--;

        if (i < 0)
        {
            i = 100;
            delta *= -1;
        }
    }

    public void OnTriggerEnter(Collider other)
    {
        if (other.transform.parent.TryGetComponent(out ArcadeKart kart))
        {
            PickUpEffect(kart.MyID);
            Destroy(gameObject);
        }
    }

    public virtual void PickUpEffect(int CarID)
    {
        // Implement This in Child Class
    }
}