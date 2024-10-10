from tags import retrieve_trends

from controller import Runner

def main():
    
    run = Runner()
    logic = 0    
    while True:        
        
        # if logic % 5 == 4:
        # run.process_msg("summer")               
        # trends = retrieve_trends()
        trends = []
        
        f = open("tags.txt", 'r')
        tags = f.readline().split(' ')
        trends = tags[logic:logic+10]
        
        print(f"trends {trends}")
        run.loop(trends)
        
        print("sleep")
                                
        logic += 1
        import time
        
        time.sleep(60*10)
        
if __name__ == '__main__':
    main()