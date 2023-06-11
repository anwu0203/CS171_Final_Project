from BlogChain import Block, BlogChain

if __name__ == '__main__':
    blog = BlogChain()
    post_types = ['POST', 'POST', 'COMMENT', 'POST', 'COMMENT', 'POST', 'COMMENT']
    users = ['monke', 'corn', 'jesus', 'monke', 'corn', 'jesus', 'corn']
    titles = ['on sussiness', 'a small loan', 'on sussiness', '(╯°□°）╯︵ ┻━┻', 'on sussiness', 'a small loan', 'boop']
    content = ['But I was the imposter all along', 'of a million dollars', 'haha u said butt', 'aeugh', 'hee haw', 'nope', 'yeet']
    
    print(blog.get_all_posts())
    print(blog.get_user_posts('monke'))
    print(blog.get_post_content('on sussiness'))
    print(blog.get_blogchain())
    
    for i in range(7):
        if post_types[i] == 'POST':
            if blog.can_make_post(titles[i]):
                nonce = blog.find_nonce(post_types[i], users[i], titles[i], content[i])
                blog.append(post_types[i], users[i], titles[i], content[i], nonce)
                print(f'Success {i}')
            else:
                print(f'Failure {i}')
        else:
            if blog.can_make_comment(titles[i]):
                nonce = blog.find_nonce(post_types[i], users[i], titles[i], content[i])
                blog.append(post_types[i], users[i], titles[i], content[i], nonce)
                print(f'Success {i}')
            else:
                print(f'Failure {i}')
            

    print(blog.get_all_posts())
    print(blog.get_user_posts('monke'))
    print(blog.get_post_content('on sussiness'))
    print(blog.get_blogchain())