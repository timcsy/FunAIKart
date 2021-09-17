using UnityEngine;
using UnityEngine.UI;

public class Speedometer : MonoBehaviour
{
    [SerializeField]
    private Text speedText;
    [SerializeField]
    private Image speedPointer;

    void FixedUpdate()
    {
        speedText.text = GetSpeed() + " km/h";
        speedPointer.transform.rotation = Quaternion.Euler(0, 0, GetAngle());
    }

    private float GetAngle()
    {
        return ((GetSpeed() * 1.6f) - 80.0f) * -1.0f;
    }

    private float GetSpeed()
    {
        return Mathf.Round(GetComponent<Rigidbody>().velocity.magnitude * 10.0f) / 2.0f;
    }
}