

# @pytest.mark.asyncio
# async def test_user_create(self, client, init_db, user_to_create):
#     response = await client.post('users/create', json=user_to_create.dict())
#     assert response.status_code == 200
#     data = response.json()
#     assert data['username'] == user_to_create.username
#     await self.remove_user(user_to_create=user_to_create)

# @pytest.mark.asyncio
# async def test_user_create_twice(self, client, init_db, user_to_create):
#     with pytest.raises(UniqueViolationError) as db_error:
#         await client.post('users/create', json=user_to_create.dict())
#         await client.post('users/create', json=user_to_create.dict())

#     assert 'duplicate key value violates unique constraint' in str(db_error.value)
#     await self.remove_user(user_to_create=user_to_create)


# @pytest.mark.asyncio
# async def test_user_create_wrong_email_format(self, client, init_db, user_to_create):
#     wrong_user = UserCreate(
#         email="wrong.user@gmail.com",
#         username="wrong_user",
#         password="wrong_user_password"
#     )

#     wrong_user.email = 'wrong_email'
#     res = await client.post('users/create', json=wrong_user.dict())
#     print(res.json())
#     assert 'value is not a valid email address' == res.json()['detail'][0]['msg']

# @pytest.mark.asyncio
# async def test_user_create_wrong_username_format(self, client, init_db, user_to_create):
#     wrong_user = UserCreate(
#         email="wrong.user@gmail.com",
#         username="wrong_user",
#         password="wrong_user_password"
#     )

#     wrong_user.username = 'asd_sad$?'
#     res = await client.post('users/create', json=wrong_user.dict())
#     print(res.json())
#     assert 'Invalid characters in username.' == res.json()['detail'][0]['msg']

# @pytest.mark.asyncio
# async def test_user_create_wrong_password_format(self, client, init_db, user_to_create):
#     wrong_user = UserCreate(
#         email="wrong.user@gmail.com",
#         username="wrong_user",
#         password="wrong_user_password"
#     )

#     wrong_user.password = '13'
#     res = await client.post('users/create', json=wrong_user.dict())
#     print(res.json())
#     assert 'ensure this value has at least 7 characters' == res.json()['detail'][0]['msg']





