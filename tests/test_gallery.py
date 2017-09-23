# def test_add_post(client, session):
#     img_path = 'benwaonline/static/benwas/test.png'
#     preview_path = 'benwaonline/static/benwas/preview.png'
#     add_post(img_path, preview_path)

#     post = Post.query.first()

#     # Dog I hate paths
#     # assert post.image.filepath == os.path.relpath(img_path, 'benwaonline/static/')
#     # assert post.preview.filepath == preview_path
#     # Figure out better way to check if List of tags contains name of
#     assert post.tags[0].name == 'benwa'

# def test_add_posts(session):
#     img_path = 'benwaonline/static/benwas/imgs'
#     preview_path = 'benwaonline/static/benwas/thumbs'
#     add_posts(img_path, preview_path)

#     posts = Post.query.all()
#     for post in posts:
#         print(post.tags.count)
#         _, img_tail = os.path.split(post.image.filepath)
#         print(img_tail)
#         _, preview_tail = os.path.split(post.preview.filepath)
#         print(preview_tail)

#         assert img_tail == preview_tail
#         # assert post.preview.filepath == preview_path
#         assert post.tags[0].name == 'benwa'