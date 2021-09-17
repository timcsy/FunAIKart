public class TurtlePickUp : PickUpClass
{
    public override void PickUpEffect(int CarID)
    {
        PickUpManager.instance.PickUp(PickUpManager.PickUpType.Turtle, CarID);
    }
}