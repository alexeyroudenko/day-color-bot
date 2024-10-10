from tags import retrieve_trends

from controller import Runner

def main():
    
    run = Runner()
    logic = 0    
    import time
    
    f = open("tags.txt", 'r')
    tags = f.readline().split(' ')        
    while True:        
        
        # if logic % 2 == 0:     
        #     word = tags[logic+7 % len(tags)]   
        #     run.process_msg(word)               
        # print("sleep")
        # time.sleep(60*2)
        
        # trends = []
        #trends = retrieve_trends()        
        trends = tags[logic:logic+10]
        print(f"trends {trends}")
        run.loop(trends)
        
        print("sleep")
        time.sleep(60*2)
        logic += 1        
        
if __name__ == '__main__':
    main()