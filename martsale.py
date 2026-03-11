import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score

data={
'Item_type':['Dairy','soft drinks','Meat','Nuts','Fruits','Snacks','Dairy','Meat','Nuts','Fruits','soft drinks','Meat','Vegtables','Nuts','Vegtables'],
'Item_visiblity':[0.012,0.016,0.045,0.019,0.032,0.030,0.021,0.017,0.035,0.010,0.013,0.047,0.044,0.025,0.027],
'Outlet_size':['Small','Medium','High','Medium','Small','High','Small','Medium','Small','High','Small','Medium','High','Small','Medium'],
'Outlet_Location_type':['Tier1','Tier2','Tier3','Tier1','Tier2','Tier3','Tier1','Tier2','Tier3','Tier1','Tier2','Tier3','Tier1','Tier2','Tier3'],
'Item_wt':[9.3,5.9,17.5,19.2,8.9,10.5,11.5,12.3,13.5,7.4,8.9,6.9,14.5,18.8,9.7],
'sales':[3735,2650,2150,3400,2400,2200,2500,2600,3525,3333,4245,2700,2900,3100,3235]
}

df=pd.DataFrame(data)

le_item=LabelEncoder()
le_size=LabelEncoder()
le_loc=LabelEncoder()

df['Item_type']=le_item.fit_transform(df['Item_type'])
df['Outlet_size']=le_size.fit_transform(df['Outlet_size'])
df['Outlet_Location_type']=le_loc.fit_transform(df['Outlet_Location_type'])

X=df.drop('sales',axis=1)
y=df['sales']

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.1,random_state=42)

model=RandomForestRegressor(n_estimators=300,max_depth=10,random_state=42)
model.fit(X_train,y_train)

pred=model.predict(X_test)
score=r2_score(y_test,pred)
print('accuracy score:',score)

for i,item in enumerate(le_item.classes_):
    print(i,'=',item)
for i,item in enumerate(le_size.classes_):
    print(i,'=',item)
for i,item in enumerate(le_loc.classes_):
    print(i,'=',item)
e=1
while e!=0:
    item_type=int(input('enter your product type:'))
    item_visiblity=float(input('enter item visiblity:'))
    outlet_size=int(input('enter your outlet_size:'))
    outlet_location=int(input('enter outlet location:'))
    item_wt=float(input('enter your product weight:'))

    new_data=pd.DataFrame([[item_type,item_visiblity,outlet_size,outlet_location,item_wt]],columns=X.columns)

    a=model.predict(new_data)
    print('prediction sales:',a[0])
      
