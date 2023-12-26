using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RotateCubeA : MonoBehaviour
{
    public float angle;
   public void Rotate(float value) {
       angle = -value;
   }

   private void Update() {
    transform.eulerAngles = new Vector3( 0f, 0f, angle);
   }
}