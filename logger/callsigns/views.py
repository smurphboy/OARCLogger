from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from logger.models import User, db