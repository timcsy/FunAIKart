using UnityEngine;
using UnityEngine.UI;

public class SingleUI : MonoBehaviour
{
    [Header("UI")]
    [SerializeField]
    private Image wheelBar;
    [SerializeField]
    private Image gasBar;
    [SerializeField]
    private Transform boostGrid;
    [SerializeField]
    private Text speedText;
    [SerializeField]
    private Image speedPointer;

    [Header("Prefab")]
    [SerializeField]
    private GameObject pfBoostUI;

    private PAIAKartAgent m_Kart;

    void Update()
    {
        m_Kart = GetComponent<PAIAKartAgent>();
    }

    public void UpdateRefill(float wheel, float gas)
    {
        wheelBar.fillAmount = wheel;
        gasBar.fillAmount = gas;
    }

    public void ApplyEffect(PickUpType type, float duration)
    {
        if (pfBoostUI != null && boostGrid != null)
        {
            GameObject pf = Instantiate(pfBoostUI, boostGrid);
            switch (type)
            {
                case PickUpType.Nitro:
                    pf.GetComponent<BoostUI>().Initialize(duration, Color.cyan, "N");
                    break;
                case PickUpType.Turtle:
                    pf.GetComponent<BoostUI>().Initialize(duration, Color.green, "T");
                    break;
                case PickUpType.Banana:
                    pf.GetComponent<BoostUI>().Initialize(duration, Color.yellow, "B");
                    break;
            }
        }
    }

    void FixedUpdate()
    {
        speedText.text = GetSpeed() + " km/h";
        speedPointer.transform.rotation = Quaternion.Euler(0, 0, GetAngle());
    }

    private float GetAngle()
    {
        return ((GetSpeed() * 1.6f) - 80.0f) * -1.0f;
    }

    private int GetSpeed()
    {
        return Mathf.RoundToInt(GetComponent<PAIAKartAgent>().velocity);
    }
}