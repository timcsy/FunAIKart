public class WheelPickUp : PickUpClass
{
    public override void PickUpEffect(PAIAKartAgent kart)
    {
        PickUpManager.instance.PickUp(PickUpType.Wheel, kart);
    }
}