def test_login_page_contains_forgot_password_option(
    client,
):
    response = client.get("/login")

    assert response.status_code == 200
    assert "CodeBusters Login" in response.text
    assert "Forgot Password?" in response.text
    assert "/auth/login" in response.text
    assert "/password-reset/initiate" in response.text
    assert "/password-reset/confirm" in response.text
