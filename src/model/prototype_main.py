import zmq
import pandas_zmq as pdzmq

PORT1 = 5556

def main():
    context1 = zmq.Context()
    socket1 = context1.socket(zmq.REQ)
    socket1.connect(f"tcp://localhost:{PORT1}")
    
    # do something
    coordinates = "44.5646, -123.2620"
    
    # send out microservice request
    socket1.send_string(f"search_location_{coordinates}") # must be in decimal degrees
    
    # receive microservice df
    response_df = pdzmq.recv_dataframe(socket1)
    print(response_df)
    
    # terminate
    socket1.send_string("end")
    socket1.recv_string()
    socket1.close()
    context1.term()
    

    

if __name__ ==  "__main__":
    main()