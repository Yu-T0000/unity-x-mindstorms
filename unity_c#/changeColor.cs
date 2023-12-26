using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class changeColor : MonoBehaviour
{


    public void Change_Color(string value)
    {
        string color = value;

        switch(color){
            case "NONE":
                GetComponent<Renderer>().material.color = Color.gray;
                break;
            case "RED":
                GetComponent<Renderer>().material.color = Color.red;
                break;
            case "BLUE":
                GetComponent<Renderer>().material.color = Color.blue;
                break;
            case "YELLOW":
                GetComponent<Renderer>().material.color = Color.yellow;
                break;
            case "GREEN":
                GetComponent<Renderer>().material.color = Color.green;
                break;
            case "WHITE":
                GetComponent<Renderer>().material.color = Color.white;
                break;
        }
        
    }
}
