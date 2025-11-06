import zmq
import pandas_zmq as pdzmq
import pandas as pd

PORT1 = 5556

def main():
    context1 = zmq.Context()
    socket1 = context1.socket(zmq.REQ)
    socket1.connect(f"tcp://localhost:{PORT1}")
    
    while(1):
        # do something
        coordinates = "44, -123"
        
        # send out microservice request
        socket1.send_string(f"search_location_{coordinates}") # must be in decimal degrees
        
        # receive microservice df
        response_df = pdzmq.recv_dataframe(socket1)
        if response_df.empty:
            print("Microservice could not find info for your location")
        else:
            print(response_df)
        
        i = input("e to end: ")
        if(i == "e"):
            break
        
    
    # terminate
    socket1.send_string("end")
    socket1.recv_string()
    socket1.close()
    context1.term()
    

    

if __name__ ==  "__main__":
    main()