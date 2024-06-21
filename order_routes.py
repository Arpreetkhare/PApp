from fastapi import APIRouter,Depends,status
from fastapi_jwt_auth import AuthJWT
from models import User,Order
from schemas import OrderModel,OrderStatusModel
from fastapi.exceptions import HTTPException
from database import Session,engine
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder




order_router=APIRouter(

    prefix='/orders',
    tags=['orders']
)

session=Session(bind=engine)

@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token ")   

    return {"message":"hello world"}

@order_router.post('/order',status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token")   


    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()

    new_order=Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,

    )

    new_order.user=user# associates new order o a current user
    session.add(new_order)#adds new order to a database
    session.commit()

    response={

        "pizza_size":new_order.pizza_size,
        "quantity":new_order.quantity,
        "id":new_order.id,
        "order_status":new_order.order_status
    } 

    return jsonable_encoder(response)


@order_router.get('/orders')
async def list_all_orders(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid token')
    

    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()

    if user.is_staff:
        orders=session.query(Order).all()

        return jsonable_encoder(orders)
    
    raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You are not a superuser')
    

        

@order_router.get('/user/orders')    

async def get_user_orders(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid token')
    

    current_user=Authorize.get_jwt_subject()

    user= session.query(User).filter(User.username==current_user).first()

    return jsonable_encoder(user.orders)



@order_router.get('user/order/{id}/',response_model=OrderModel)

async def get_specific_order(id:int,Authorize:AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid token')
    
    current_user=Authorize.get_jwt_subject()
    user= session.query(User).filter(User.username==current_user).first()

    orders=user.orders

    for o in orders:
        if o.id==id:
            return jsonable_encoder(o)
        
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST
                        ,detail='No order with such id')    

   

@order_router.put('/order/update/{order_id}/') 
async def update_order(id:int,order:OrderModel,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='invalid token')
    

    order_to_update=session.query(Order).filter(Order.id==id).first()

    order_to_update.quantity=order.quantity
    order_to_update.pizza_size=order.pizza_size
    session.commit()

    response={
            "id":order_to_update.id,
            "quantity":order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status":order_to_update.order_status
        }

    

    return jsonable_encoder(order_to_update)


@order_router.patch('/order/update/{id}/')

async def update_order_status(id:int,order:OrderStatusModel,Authorize:AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                            ,detail='invalid token')
    
    current_user=Authorize.get_jwt_subject()

    user= session.query(User).filter(User.username==current_user).first()

    if user.is_staff:
        order_to_update=session.query(Order).filter(Order.id==id).first()

        order_to_update.order_status=order.order_status
        session.commit() 

        response={
            "id":order_to_update.id,
            "quantity":order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status":order_to_update.order_status
        }

        return jsonable_encoder(response)
    

@order_router.delete('/order/delete/{id}/',status_code=status.HTTP_204_NO_CONTENT)    

async def delete_an_order(id:int,Authorize:AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
                            ,detail='invalid token')
    
    current_user=Authorize.get_jwt_subject()

    order_to_delete=session.query(Order).filter(Order.id==id).first()

    if order_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Order not found')

    if order_to_delete.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail='Not authorized to delete this order')


    session.delete(order_to_delete)

    session.commit()
    return order_to_delete



    
  
