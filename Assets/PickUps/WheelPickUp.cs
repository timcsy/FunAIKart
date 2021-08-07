public class WheelPickUp : PickUpClass
{
    public override void PickUpEffect(int CarID)
    {
        PickUpManager.instance.PickUp(PickUpManager.PickUpType.Wheel, CarID);
    }
}