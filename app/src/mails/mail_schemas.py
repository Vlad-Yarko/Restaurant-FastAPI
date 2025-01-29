def authorization_code(
        action: str,
        email: str,
        code: str,
):

    return f"""
<html>
    <body>
        <h1>Hello dear {email}</h1>
        <h5>You have been on our website and wanted to {action} your account</h5>
        <p>We are very happy about you, nice to meet you</p>
        <p>But first of all you must verify your email address</p>
        <h1>{code}</h1>
        <h3>So above you can see this code</h3>
        <h3>Please keep it safe and do not give it to third parties</h3>
    </body>
</html>
"""
