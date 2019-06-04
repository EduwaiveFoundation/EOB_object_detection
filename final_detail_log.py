import pandas as pd
import glob , os , csv , sys

def merge_csv(path , exp_no):
    final = pd.read_csv("actual.csv")
    classes=os.listdir(path)
    with open("out.csv","w") as f:    
        for class_ in classes:
	    wr = csv.writer(f,delimiter="\n")
	    wr.writerow(glob.glob(os.path.join(path,class_, "*.pdf")))
    
    df = pd.read_csv("out.csv" , header=None)
    df.columns=['name']
    new = df["name"].str.split("/", n = 0, expand = True) 
    # making seperate first name column from new data frame 
    df["exp_no"]= new[1] 
    df["name"] = new[2]
    df.sort_values(['name','exp_no'], ascending=True , inplace=True)
    final= pd.merge(final,df,on="name",how="inner")
    final.to_csv("actual.csv", index=False)


path = str(sys.argv[1])
exp_no = str(sys.argv[2])
merge_csv(path,exp_no)



